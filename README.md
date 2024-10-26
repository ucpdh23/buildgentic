# buildgentic

This project is a POC of an Agentic AI system to create Agentic AI softwares.
This project is compose by several agents:
- *Manager* this agent is responsible of transforming the business requirement into development activities by creating tasks.
- *Developer* this agent is responsible of develop the code changes.

This system interacts with *servant* for several actions:
- To run the agent. servant publish the message with the required information
- To interact with some external systems such as Workitems in AzureDevOps and the github repo.


# building

Use this command to create the package:
python setup.py sdist bdist_wheel

