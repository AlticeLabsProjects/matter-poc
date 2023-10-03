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
- How to debug an issue with local automation?
  - solution: provide an API to export Logs to customer care
  
### references

https://www.youtube.com/watch?v=H7OIHueCmSs

https://opensource.com/article/20/11/cloud-vs-local-home-automation

https://homeseer.com/cloud-vs-locally-managed-smart-home-hubs/

