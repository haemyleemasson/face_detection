# This code is modifed version (Haemy Lee Masson, 09-2020) of a sample code provided by Amazon.com.  
# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

import boto3
import json
import sys
import time

class VideoDetect:
    jobId = ''
    rek = boto3.client('rekognition')
    sqs = boto3.client('sqs')
    sns = boto3.client('sns')
    # leave them blank, you will need to copy these information at the bottom. 
    roleArn = '' 
    bucket = ''
    video = ''
    startJobId = ''
    sqsQueueUrl = ''
    snsTopicArn = ''
    processType = ''

    def __init__(self, role, bucket, video):    
        self.roleArn = role
        self.bucket = bucket
        self.video = video

    def GetSQSMessageSuccess(self):

        jobFound = False
        succeeded = False
    
        dotLine=0
        while jobFound == False:
            sqsResponse = self.sqs.receive_message(QueueUrl=self.sqsQueueUrl, MessageAttributeNames=['ALL'],
                                          MaxNumberOfMessages=10)

            if sqsResponse:
                
                if 'Messages' not in sqsResponse:
                    if dotLine<40:
                        print('.', end='')
                        dotLine=dotLine+1
                    else:
                        print()
                        dotLine=0    
                    sys.stdout.flush()
                    time.sleep(5)
                    continue

                for message in sqsResponse['Messages']:
                    notification = json.loads(message['Body'])
                    rekMessage = json.loads(notification['Message'])
                    print(rekMessage['JobId'])
                    print(rekMessage['Status'])
                    if rekMessage['JobId'] == self.startJobId:
                        print('Matching Job Found:' + rekMessage['JobId'])
                        jobFound = True
                        if (rekMessage['Status']=='SUCCEEDED'):
                            succeeded=True

                        self.sqs.delete_message(QueueUrl=self.sqsQueueUrl,
                                       ReceiptHandle=message['ReceiptHandle'])
                    else:
                        print("Job didn't match:" +
                              str(rekMessage['JobId']) + ' : ' + self.startJobId)
                    # Delete the unknown message. Consider sending to dead letter queue
                    self.sqs.delete_message(QueueUrl=self.sqsQueueUrl,
                                   ReceiptHandle=message['ReceiptHandle'])


        return succeeded
       
    def StartFaceDetection(self): # face detection
        response=self.rek.start_face_detection(Video={'S3Object': {'Bucket': self.bucket, 'Name': self.video}},
            NotificationChannel={'RoleArn': self.roleArn, 'SNSTopicArn': self.snsTopicArn}, FaceAttributes='ALL')

        self.startJobId=response['JobId']
        print('Start Job Id: ' + self.startJobId)

    def GetFaceDetectionResults(self): # get results
        maxResults = 1000
        paginationToken = ''
        finished = False
        results = []
        while finished == False:
            response = self.rek.get_face_detection(JobId=self.startJobId,
                                            MaxResults=maxResults,NextToken=paginationToken)
                                            
            # video file information 
            print('Codec: ' + response['VideoMetadata']['Codec'])
            print('Duration: ' + str(response['VideoMetadata']['DurationMillis']))
            print('Format: ' + response['VideoMetadata']['Format'])
            print('Frame rate: ' + str(response['VideoMetadata']['FrameRate']))
            print()
                    
            for faceDetection in response['Faces']:
                results.append({"face": faceDetection['Face'], "time": faceDetection['Timestamp']})

            if 'NextToken' in response:
                paginationToken = response['NextToken']
            else:
                with open(self.startJobId + "_faces.json", "w") as output:
                     json.dump(results, output) # write the results in json file format.
                finished = True    
            

    def CreateTopicandQueue(self):
      
        millis = str(int(round(time.time() * 1000)))

        #Create SNS topic
        
        snsTopicName="AmazonRekognitionSherlock" + millis

        topicResponse=self.sns.create_topic(Name=snsTopicName)
        self.snsTopicArn = topicResponse['TopicArn']

        #create SQS queue
        sqsQueueName="AmazonRekognitionSherlock" + millis
        self.sqs.create_queue(QueueName=sqsQueueName)
        self.sqsQueueUrl = self.sqs.get_queue_url(QueueName=sqsQueueName)['QueueUrl']
 
        attribs = self.sqs.get_queue_attributes(QueueUrl=self.sqsQueueUrl,
                                                    AttributeNames=['QueueArn'])['Attributes']
                                        
        sqsQueueArn = attribs['QueueArn']

        # Subscribe SQS queue to SNS topic
        self.sns.subscribe(
            TopicArn=self.snsTopicArn,
            Protocol='sqs',
            Endpoint=sqsQueueArn)

        #Authorize SNS to write SQS queue 
        policy = """{{
  "Version":"2012-10-17",
  "Statement":[
    {{
      "Sid":"MyPolicy",
      "Effect":"Allow",
      "Principal" : {{"AWS" : "*"}},
      "Action":"SQS:SendMessage",
      "Resource": "{}",
      "Condition":{{
        "ArnEquals":{{
          "aws:SourceArn": "{}"
        }}
      }}
    }}
  ]
}}""".format(sqsQueueArn, self.snsTopicArn)
 
        response = self.sqs.set_queue_attributes(
            QueueUrl = self.sqsQueueUrl,
            Attributes = {
                'Policy' : policy
            })

    def DeleteTopicandQueue(self):
        self.sqs.delete_queue(QueueUrl=self.sqsQueueUrl)
        self.sns.delete_topic(TopicArn=self.snsTopicArn)


def main():
    roleArn = 'YOUR ROLE ARN'   
    bucket = 'YOUR BUCKET NAME'
    video = 'YOUR VIDEO NAME'
    analyzer=VideoDetect(roleArn, bucket,video)
    analyzer.CreateTopicandQueue()
    analyzer.StartFaceDetection()
    if analyzer.GetSQSMessageSuccess()==True:
        analyzer.GetFaceDetectionResults()
    
    analyzer.DeleteTopicandQueue()



if __name__ == "__main__":
    main()