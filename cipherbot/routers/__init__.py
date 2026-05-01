from . import analyze, common, decrypt, detect, encrypt, export, genkey, history

routers = [
    common.router,
    encrypt.router,
    decrypt.router,
    detect.router,
    analyze.router,
    genkey.router,
    history.router,
    export.router,
]

__all__ = ["routers"]
