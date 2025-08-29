from urllib.request import Request, urlopen
from tarfile import open as taropen
from shutil import rmtree, copytree
from zipfile import ZipFile
from pathlib import Path
from json import loads


def log(message):
    print(f"=> {message}")


token = Path("token.txt")
if token.exists():
    HEADERS = {"Authorization": f"token {token.read_text().strip()}", "User-Agent": "HATS-Pack-Script"}
    log("Using GitHub token authentication")
else:
    HEADERS = {"User-Agent": "HATS-Pack-Script"}
    log("Running anonymously (missing token.txt)")


def get(uri):
    req = Request(uri, headers=HEADERS)
    with urlopen(req) as response:
        return response.read()

def get_json(uri):
    return loads(get(uri).decode("utf-8"))

def download(uri, dest_folder):
    filename = uri.split("/")[-1]
    dest_path = dest_folder / filename
    dest_path.write_bytes(get(uri))
    return dest_path

build = open('build.txt', 'w')

log("Cleaning environment...")
package = Path("package")
rmtree(package, ignore_errors=True)
package.mkdir()

log("Getting latest bootloader...")
releases = get_json("https://api.github.com/repos/ctcaer/hekate/releases")
assets = get_json(f"https://api.github.com/repos/ctcaer/hekate/releases/{releases[0]['id']}/assets")
hekate_url = [a for a in assets if a["name"].startswith("hekate")][0]["browser_download_url"]
build.write(f'hekate_ver={releases[0]['tag_name'].split("v")[1]}\n')

releases = get_json("https://api.github.com/repos/Atmosphere-NX/Atmosphere/releases")
assets = get_json(f"https://api.github.com/repos/Atmosphere-NX/Atmosphere/releases/{releases[0]['id']}/assets")
atmosphere_url = [a for a in assets if a["name"].startswith("atmosphere")][0]["browser_download_url"]
build.write(f'atmosphere_ver={releases[0]['tag_name']}\n')

log("Downloading and unzipping files...")
hekate_zip = download(hekate_url, package)
ZipFile(hekate_zip, "r").extractall(package)
hekate_zip.unlink()
atmosphere_zip = download(atmosphere_url, package)
ZipFile(atmosphere_zip, "r").extractall(package)
atmosphere_zip.unlink()

for bin in package.glob("hekate*.bin"):
    bin.rename(package / "payload.bin")

log("Cleaning files...")
atmosphere = package / "atmosphere"
bootloader = package / "bootloader"
switch = package / "switch"

for dir in [
    atmosphere/"config_templates",
    atmosphere/"hbl_html",
    atmosphere/"kip_patches",
    bootloader/"ini",
    bootloader/"payloads",
    bootloader/"res",
    bootloader/"sys"/"l4t"  # Keep if wanna use Linux
]:
    rmtree(dir, ignore_errors=True)

for file in [
    atmosphere/"hbl.nsp",
    bootloader/"update.bin",
    switch/"daybreak.nro",
    switch/"haze.nro",
    switch/"reboot_to_payload.nro"
]:
    file.unlink()

log("Copying new files...")
copytree("sdcard", "package", dirs_exist_ok=True)

log("Compressing archive...")
taropen("package.tar.xz", "w:xz", preset=9).add(package, arcname=package.name)
rmtree(package, ignore_errors=True)

print("Done")
exit(0)
