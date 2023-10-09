# Local control vs Cloud control

PROS Local / CONS Cloud

- more privacy friendly (personal data not transferred to Cloud)
- responsive system with lower latency in devices communication
- more resilient to Internet access problems
- simpler arch:
  - more agile to evolve
  - easier to debug 
- lower impact of failures (locally) e.g. if scheduller fails it only impacts a single home
- Better SLAs
- Future proof / longevity: the system is owned by the user and should still work without the service provider
- More secure (?)
- less cloud resources spent

CONS Local / PROS Cloud

- more resources spent locally, more expensive controllers
- AI based intelligence needs lots of computing resources
- Ask authorisation for remote access to debug local system
- more challenging to be proactive on local failures

### Challenges

- If we need Backup of the Controller data / status isn't it breaking privacy?
  - answer: data is encrypted and should only contain required data to recover Matter Controller and Automation scripts
- How to debug an issue with local automation?
  - answer: provide an API to export Logs to customer care / support team
- FiberGW does not have enough computing resources
  - answer: only the mandatory Matter stack is in the FiberGW docker runtime and the remaing software component containing app level controller components including automation is in a separated docker image hosted in the Cloud. The two images should transparemtly communicate each other taking advantage of containarisation abstration runtime. To keep a clean separation of concerns, integration with non-Matter protocols would be provided using bridge / integration components hosted in a separated docker image.
- Local failures are not possible to detect or prevent in a proactive way
  - answer: some monitoring of local resources would be needed triggering alarms to the cloud, similar to what is in place today with the FibeGW
- AI based intelligence needs lots of computing resources
  - answer: more advanced intelligence (eg using LLM models a la ChatGPT) can be delivered based on the cloud in an autonomous way based on events feeding some kind of datalake. For privacy reasons, by default these features would be disabled and the end-user would have to give permissions. Furthermore, since this is spending more resources to deliver more advanced features, it can be delivered as a premium feature to end-users.

### references

https://www.youtube.com/watch?v=H7OIHueCmSs

https://opensource.com/article/20/11/cloud-vs-local-home-automation

https://homeseer.com/cloud-vs-locally-managed-smart-home-hubs/

