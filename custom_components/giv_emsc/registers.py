"""
Register map for GIV-EMS-C.

Addresses are stored in a compressed, encoded blob so they are not
visible as plain text in the source. Decoded once at runtime.
Regenerate the blob with: python scripts/encode_registers.py
"""

import base64
import json
import zlib
from dataclasses import dataclass
from typing import Dict, Optional

_REGISTER_BLOB = (
    "c-p0yO>d((7{|Ygg|xS77f3QQ=`Bf{?MTfgDpB@`958_?FIi*AWJmq(YYYTqOp4hadhmn(KX~4q"
    "Us`~*$6uOW{EK0Pv_}m^shtu?vQ&G}T$DQW?0I7Wt3FE|7}5ug2Q7;OLaoJFaEg(uJ$f)q(Z_>"
    "kaDwODu=6A&@Pr!0-GK_?AU**D9B#%+TK~NfKS<Qgmb!UQ-Beefaq1@=xV5|u8^E9RyjBJ~AEp"
    "Q_h7-Q@5sr5W%i)BteFWz&VKtoaO^C3QVT@uTkMQbdl&CKx>T@B&chpUFb%W3MAkJ%f8#jROag"
    "H!S7`)ZKQKlF@lvF~oMpMil3XxFuqbU<Hp*)QK$x!TEg@jsj=QnY^QGfYYCeK&IIk_Ngd(a_?E"
    "FQbU4A!-|Vd(cel9;dzBTv^|Ws*4O{cl-6(uH*G)i%|&r$T(`hX*+l5jXcNn0YXU;EYi^O%MG%"
    "CzxhY;zBXR&&&j#V}wsvu&<twl6(oO)BS>|7xg{*Kd6Z=q6Duo#;zbJ`fD;1tImg*wpZaBZc$k="
    "^XTv3+o1=ukl0S*BHIs6etSr-3nN%jBX}u|L#Fjqm+ObgrC0uy*#@ce9V$#<Ckn6hOf>*gu`Jv"
    "m{UioY^%G;mFy+ILUQ>c1JEFd5SQa}3oAPjob7s8jkC4z8y>|DReL`RemZf?4MpM1_%#biT6Sd"
    "74JRxd^DPah4ZW9y(KAW@v&U<$5`f16|0ZXWDM$Q=-vHnfFAjz<kphk_p8J|>;rfRXJrHRu?sz"
    "qr7)^;V!t=~G@RNU`u_b$o<ht|mTj985~m?vfddum}7J}`m#*LM>-H)41UdD-m~t+(oIh+u0zR"
    "8uGnqJY>r3^Pu-8bhyz4U!;<!J&F!=xl8jA3s-Z3<>&VxPrIxnE{ayviIzyb`sl(=W#2-$^zT?k"
    "FDpii`L-w!8@yIf%N`Hy=L&)S{7Z?1Fhl_un!^x3>oa@WwVh1ze<59cJJe!V|N5>-UDl=n2e^7"
    "aC5%k`y9Af)iZpg<L0w2Metg~80D?`7a5`LDjuQWBEyi4DU4EtbD>++!FVf;!`oFsF}h#SuEg7"
    "TDnCM{1dY~BsmUfepvff_hN;uPZu=^GN_q*1<IDS3)l#hbkwJ};vWz|$>zEB|1Ao?2s@i!~Z#cT"
    "%`qc%&ce+B5&PVO2fi4e(6t^AK&oRx;H4wT#*s$UV%u@^ZN0yR^t|)9`DKMtuouEAinR^uGUm-"
    "aYn!A%^{ANX`Mn)H(zq05^-#qaEZT1T4d|4l(&()V374>h@!DJsvEFDfu8rmctu0JvQ8%J-`P$;"
    ")a`*Lw9nvv}#nC>`^f8y^Lm!cJcbz!R8$7@w2Lt(9bft5h&!<=S%=fYo9fmPbZ)LLs}r)y7$uC"
    "^D1p~yKf6IfG|I_cx%Ke!9~sQ"
)

_cache: Optional[Dict] = None


def _load() -> Dict:
    global _cache
    if _cache is None:
        raw = base64.b85decode(_REGISTER_BLOB)
        _cache = json.loads(zlib.decompress(raw))
    return _cache


@dataclass
class RegisterDef:
    address: int
    name: str
    desc: str
    scale: float
    unit: str
    signed: bool

    def decode(self, raw: int) -> float:
        if self.signed and raw > 32767:
            raw -= 65536
        return round(raw * self.scale, 6)

    def encode(self, value: float) -> int:
        """Convert an engineering value back to a raw Modbus word."""
        raw = round(value / self.scale)
        if self.signed and raw < 0:
            raw += 65536
        return int(raw) & 0xFFFF


def input_registers() -> Dict[int, RegisterDef]:
    return {
        int(k): RegisterDef(int(k), v["name"], v["desc"], v["scale"], v["unit"], v["signed"])
        for k, v in _load()["ir"].items()
    }


def holding_registers() -> Dict[int, RegisterDef]:
    return {
        int(k): RegisterDef(int(k), v["name"], v["desc"], v["scale"], v["unit"], v["signed"])
        for k, v in _load()["hr"].items()
    }


def by_name(name: str) -> Optional[RegisterDef]:
    for reg in {**input_registers(), **holding_registers()}.values():
        if reg.name == name:
            return reg
    return None
