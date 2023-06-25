import boto3

cloudwatch = boto3.client('cloudwatch')


def publish_metrics(metric_name: str, namespace: str = 'VATSIM_Data_Collector', value: int = 1):
    response = cloudwatch.put_metric_data(
        Namespace=namespace,
        MetricData=[
            {
                'MetricName': metric_name,
                'Unit': 'Count',
                'Value': value
            },
        ]
    )
