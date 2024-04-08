def awsAccountId = '160472638876'
def awsRegion = 'us-east-2'
def repoName = 'SampleMERNwithMicroservices'
def ecrUrl = "${awsAccountId}.dkr.ecr.${awsRegion}.amazonaws.com"
def awsCredentialsId = 'aws-credentials'

job("${repoName}-frontend-build") {
    scm {
        git {
            remote {
                url('https://git-codecommit.${awsRegion}.amazonaws.com/v1/repos/${repoName}')
                credentials(awsCredentialsId)
            }
            branch('main')
        }
        // Poll SCM to check for changes every 5 minutes
        triggers {
            scm('H/5 * * * *')
        }
    }
    steps {
        withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: awsCredentialsId]]) {
            shell("""
                cd frontend
                docker build -t ${ecrUrl}/smm-frontend:latest .
                $(aws ecr get-login --no-include-email --region ${awsRegion})
                docker push ${ecrUrl}/smm-frontend:latest
            """)
        }
    }
}

job("${repoName}-hello-service-build") {
    scm {
        git('git-codecommit.${awsRegion}.amazonaws.com/v1/repos/${repoName}', 'master')
        triggers {
            scm('H/5 * * * *')
        }
    }
    steps {
        withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: awsCredentialsId]]) {
            shell("""
                cd backend/helloService
                docker build -t ${ecrUrl}/smm-hello-service:latest .
                $(aws ecr get-login --no-include-email --region ${awsRegion})
                docker push ${ecrUrl}/smm-hello-service:latest
            """)
        }
    }
}

job("${repoName}-profile-service-build") {
    scm {
        git('git-codecommit.${awsRegion}.amazonaws.com/v1/repos/${repoName}', 'master')
        triggers {
            scm('H/5 * * * *')
        }
    }
    steps {
        withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: awsCredentialsId]]) {
            shell("""
                cd backend/profileService
                docker build -t ${ecrUrl}/smm-profile-service:latest .
                $(aws ecr get-login --no-include-email --region ${awsRegion})
                docker push ${ecrUrl}/smm-profile-service:latest
            """)
        }
    }
}
