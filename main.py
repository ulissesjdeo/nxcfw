from urllib.request import Request, urlopen
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
    open(dest_path, "wb").write(get(uri))
    return package.joinpath(filename)

releases = get_json("https://api.github.com/repos/ctcaer/hekate/releases")
assets = get_json(f"https://api.github.com/repos/ctcaer/hekate/releases/{releases[0]["id"]}/assets")

url = [a for a in assets if a["name"].startswith("hekate")][0]["browser_download_url"]

hekate = download(url, package)

del url, assets, releases

pass
