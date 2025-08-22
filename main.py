from urllib.request import Request, urlopen
from zipfile import ZipFile
from shutil import rmtree
from pathlib import Path
from json import loads

package = Path("package")
rmtree(package, ignore_errors=True)
package.mkdir()

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

releases = get_json("https://api.github.com/repos/ctcaer/hekate/releases")
assets = get_json(f"https://api.github.com/repos/ctcaer/hekate/releases/{releases[0]['id']}/assets")

url = [a for a in assets if a["name"].startswith("hekate")][0]["browser_download_url"]

hekate_zip = download(url, package)
ZipFile(hekate_zip, "r").extractall(package)
hekate_zip.unlink()

del releases, assets, url, hekate_zip

bootloader = package / "bootloader"

for dir in [bootloader/"res", bootloader/"payloads", bootloader/"ini"]:
    rmtree(dir)

for file in [bootloader/"update.bin"]:
    file.unlink()

del bootloader, dir, file, package
exit(0)
