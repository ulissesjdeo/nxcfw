from urllib.request import Request, urlopen
from zipfile import ZipFile
from shutil import rmtree
from pathlib import Path
from tarfile import open
from json import loads

def log(message):
    print(f"=> {message}")

def get(uri):
    with urlopen(Request(uri)) as response:
        return response.read()

def get_json(uri):
    return loads(get(uri).decode("utf-8"))

def download(uri, dest_folder):
    filename = uri.split("/")[-1]
    dest_path = dest_folder / filename
    dest_path.write_bytes(get(uri))
    return dest_path

log("Cleaning environment...")
package = Path("package")
rmtree(package, ignore_errors=True)
package.mkdir()

log("Getting latest bootloader...")
releases = get_json("https://api.github.com/repos/ctcaer/hekate/releases")
assets = get_json(f"https://api.github.com/repos/ctcaer/hekate/releases/{releases[0]['id']}/assets")
url = [a for a in assets if a["name"].startswith("hekate")][0]["browser_download_url"]

log("Unzipping files...")
hekate_zip = download(url, package)
ZipFile(hekate_zip, "r").extractall(package)
hekate_zip.unlink()

del releases, assets, url, hekate_zip

log("Cleaning files...")
bootloader = package / "bootloader"

for dir in [bootloader/"res", bootloader/"payloads", bootloader/"ini"]:
    rmtree(dir)

for file in [bootloader/"update.bin"]:
    file.unlink()

log("Compressing archive...")
open("package.tar.xz", "w:xz", preset=9).add(package, arcname=package.name)
rmtree(package, ignore_errors=True)

del bootloader, dir, file, package, open
log("Done.")
exit(0)
