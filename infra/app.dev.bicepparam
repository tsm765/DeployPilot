using './app.bicep'

param location = 'swedencentral'
param environment = 'dev'
param projectName = 'deploypilot'

param containerImage = 'acrdeploypilotad7aew6bhs6zo.azurecr.io/deploypilot-demo:da6e96274b64e1b217ed09340e386c79fa6eb850'