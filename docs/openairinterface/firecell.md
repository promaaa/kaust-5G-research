# Firecell

## Firecell Commands
- `run-labkit deploy-5g`: start the core network.
- `run-labkit start-gnb-b210`: run gNB.
- `run-labkit stop-gnb-b210`: stop gNB.
- `run-labkit undeploy-5g`: stop the core.
- `check-labkit all`: show state of each element.
- `run-labkit`: show general information.
- `tail -f /var/log/firecell/gNB-B210.log`: show logs of gNB.
- `sudo vim /etc/conf/firecell/5G/ran/gNB.conf`: config file of the gNB.
	- also include log level.
- `cd /etc/conf/firecell/template/5G/ran/`: in this folder there are some config files for the gNB that you can use with the following command:
	- `sudo cp  gNB.N78.fr1.40MHz.TDD311.B210.conf /etc/conf/firecell/5G/ran/gNB.conf`
- `cd /etc/conf/firecell/5G/cn/conf`: contains some config files for core network.

## Update labkit code
- `git clone https://gitlab.com/firecell/support/public-firecellrd-ran.git`
- `cd public-firecellrd-ran`
- `git fetch --tags`: get latest tags
- `git tag -l`: show the tags
- `git checkout v3.3.0`: make sure you use the same version the labkit is using
	- you can know your version using: `run-labkit`
- `cd cmake_targets/`
- `sudo ./build_oai -I`
- `sudo ./build_oai -w USRP --gNB`
- Now you can edit the code and after completing run the following:
	- `cd public-firecellrd-ran/cmake_targets/`
	- `sudo ./build_oai --gNB`
- Before updating the binary file used by the labkit it's better to make a backup:
	- `sudo /usr/local/bin/firecell/fc-mgr backup`
- Make sure gNB is not active 
- Then for update:
	- If your folder is `/home/firecell/public-firecellrd-ran` you can just run:
		- `sudo /usr/local/bin/firecell/fc-mgr update`
	- If not:
		- `sudo /usr/local/bin/firecell/fc-mgr -u [source_code_path] update`
		 **NOTE:** you should put the path to build folder :
		 `/home/firecell/public-firecellrd-ran/cmake_targets/ran_build/build/`
- If you want to restore to the backup state:
	- `sudo /usr/local/bin/firecell/fc-mgr restore`

