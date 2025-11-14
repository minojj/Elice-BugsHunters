import os, shutil, subprocess

def _which(p):
    if not p: return None
    if os.path.isabs(p):
        return p if os.path.exists(p) else None
    return shutil.which(p)

def _find_driver():
    for c in (
        os.getenv("CHROMEDRIVER"),
        "chromedriver",
        "/usr/bin/chromedriver",
        "/usr/local/bin/chromedriver",
    ):
        p = _which(c)
        if p:
            return p
    return None

def _ok(p):
    try:
        return subprocess.run([p, "--version"], capture_output=True, text=True, timeout=3).returncode == 0
    except Exception:
        return False

def _patch(path):
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        from webdriver_manager.core.manager import DriverManager
    except Exception:
        return  # WDM 미사용 시 무시
    def _install(self, *args, **kwargs):
        return path  # 항상 시스템 chromedriver 반환
    ChromeDriverManager.install = _install  # type: ignore
    DriverManager.install = _install        # type: ignore
    os.environ.setdefault("WDM_LOCAL", "1")
    os.environ.setdefault("WDM_CACHE", os.path.join(os.getcwd(), ".wdm"))
    print(f"[sitecustomize] webdriver-manager patched -> {path}")

if os.getenv("CI", "false").lower() in ("1","true") or os.getenv("JENKINS_URL"):
    p = _find_driver()
    if p and _ok(p):
        _patch(p)
    else:
        print("[sitecustomize] system chromedriver not found; skip patch")