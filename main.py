from urllib.request import Request, urlopen
from shutil import rmtree
from pathlib import Path
from json import loads

package = Path("package")
rmtree(package, ignore_errors=True)
package.mkdir()

def get(url):
    with urlopen(Request(url)) as response:
        return loads(response.read().decode("utf-8"))

releases = get("https://api.github.com/repos/ctcaer/hekate/releases")
assets = get(f"https://api.github.com/repos/ctcaer/hekate/releases/{releases[0]["id"]}/assets")

url = [a for a in assets if a["name"].startswith("hekate")][0]["browser_download_url"]

del assets, releases

pass
