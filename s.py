import os
import json
import httplib
import md5

checksum_path = "/var/lib/apt-spy/checksum"
fi,fo,fe = os.popen3("apt-show-versions")
bulk = list()

for line in fo.readlines():

  id = md5.new(line).hexdigest()

  parts = line.rstrip().split(" ")
  obj = {"status": parts[1]}
  if "/" in parts[0]:
    obj["name"], obj["source"] = parts[0].split("/")
  else:
    obj["name"] = parts[0]

  if "upgradeable" == obj["status"]:
    obj["version"] = {"current": parts[3], "available":  parts[5]}
  else:
    obj["version"] = {"current": parts[2]}

  bulk.append(json.dumps({"index": {"_index": "hosting", "_type": "packages", "_id": id}}))
  bulk.append(json.dumps(obj))

bulk = "\n".join(bulk)

new_checksum = md5.new(bulk).hexdigest()

if not os.path.isfile(checksum_path):
  print('can not find checksum file in {}'.format(checksum_path))
  open(checksum_path, "w").close()

checksum_file = open(checksum_path, "r+w")
old_checksum = checksum_file.read()
checksum_file.close()


if old_checksum != new_checksum:
  print ("New updates should be notified")
  conn = httplib.HTTPConnection('localhost', 9200)
  conn.request("post", "/_bulk", bulk)
  conn.close()
else:
  print ("no update found...")

print ("writing new checksum {}").format(new_checksum)
checksum_file = open(checksum_path, "w")
checksum_file.write(new_checksum)
checksum_file.close()