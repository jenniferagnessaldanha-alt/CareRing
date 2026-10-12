# CareRing
Agentic AI care companion built on Ring events + AWS (serverless).

`web/index.html` interactive dashboard prototype (simulated data). `template.yaml` + `src/` AWS SAM backend.

## Deploy
```
pip install aws-sam-cli
sam build && sam deploy --guided --parameter-overrides FamilyPhone=+1... CHWPhone=+1... Tier2WaitSeconds=20
aws lambda invoke --function-name <Simulate> --payload '{"concerning_today":true}' --cli-binary-format raw-in-base64-out /dev/stdout
aws lambda invoke --function-name <Analyze> /dev/stdout
```
Enable the Bedrock model in the console first. Delete the stack when done: `sam delete`.
