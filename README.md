# How to use aws rekogntion (for a Mac OS or Linux user)
With this python code, you will be able to use **awe rekognition** services for analyzing a stored video. This code is initially made for face detection. The code needs slight modification when using other services (e.g., scene labeling or celebrity recognition).
# Prerequisites
1. Create/log into the AWS IAM account.
2. Go to the terminal to install CLI.

       pip install awscli
          
3. Configure CLI with Amazon credentials and region information.
    1. Go to your IAM account and create a user and specify name -> give 	
    programmatic access to this user -> give administrator access, 
    AmazonRekognitionFullAccess, AmazonS3FullAccess, AmazonSQSFullAccess, 
    AmazonSNSFullAccess. 
    2. Copy access key ID and secret access key for the aws configuration (step4).
    3. Create a role by giving it a name and AmazonRekognitionFullAccess and give Amazon Rekognition Video access to Amazon SNS topics (see document 2 number 7).
    4. **Save role ARN** -> you will need to copy this to the code!
    5. Creat **a bucket in your S3 and upload** your video/image.  
    6. **Save the bucket and the file names** -> you will need to copy this to the code!
4. Go to terminal and do the aws configuration.

       aws configure
          
     You will need to type **Access key ID, secret access key, and region information**.
     Region info:  “us-east-1”. see the link below to check your [region](https://docs.aws.amazon.com/general/latest/gr/rande.html]).
5. Install boto3.
       
       pip install boto3 (option1)
       conda install -c anaconda boto3 (option2)

If you need more information, please visit [1](https://github.com/awsdocs/amazon-rekognition-developer-guide/tree/master/code_examples/python_examples) and [2](https://docs.aws.amazon.com/rekognition/latest/dg/api-video-roles.html)
# Python Code
This code is the modified version of a sample code provided by Amazon.
At the end of the code, copy and paste the role ARN, bucket, and the file name.
Note that your video must be in the MP4 format.  
# MATLAB Code
This code is to create the onset file for the fMRI analysis. 
The face onset file is in second (not TR nor millisecond) and can be added to the first-level fMRI design matrix. 
