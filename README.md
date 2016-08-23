# PrimeGen for JUNOS
---

##### Requires:
 - Python 2.7

This script takes-in a juniper configuration that has [FIELDS] within the config that can be replaced with user-added information. It takes \configs\juniper.config, applies changes, and exports them in the same directory as \configs\prime.config. This is meant to be used in conjunction with SwitchPick for auto-provisioning.


##### Technical notes:
 - The current version is not scalable, but that it something I would like to work on if given the time. A future version could utilize Jinja to take XML/YAML files that correspond to 'blocks' of configuration templates, and could build configs out of them... not unlike Rog's script, but with superior scalability.
 - This project has a lot of potential and the implementation at this stage was very simple. It only took me like an hour or two to make & QA this.
 - This script was commisioned by Norm, my new "technical tools supervisor".