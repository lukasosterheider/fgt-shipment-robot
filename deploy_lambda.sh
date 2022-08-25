cd package
zip -r ../my-deployment-package.zip .
cd ..
zip -g my-deployment-package.zip lambda_function.py
aws lambda update-function-code --function-name FGT-WHS-PHA-Automation --zip-file fileb://my-deployment-package.zip --region eu-central-1
rm my-deployment-package.zip