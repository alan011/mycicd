ENVS = {
    "sit": {
        "k8s_master": 172.16.100.10,
    },
    "uat": {
        "k8s_master": 10.100.1.10,
    },
    "prod": {
        "k8s_master": 10.0.1.10,
    },
}

DOCKER_REPO = "docker-repo.example.com"
PACKGE_SERVER = "172.16.0.11"

APPS = {
    "company-news-static": {
        "gitlab"        : "http://gitlab.example.com/news/company-news-static.git",
        "release_branch": "master",
        "build_command" : "" ,
        "app_type"      : "static",
        "dockerfile"    : "/data1/dockerfiles/company-news-static/Dockerfile"
    },

    "company-news-java": {
        "gitlab"        : "http://gitlab.example.com/news/company-news-java.git",
        "release_branch": "master",
        "build_command" : "mvn compile"
        "app_type"      : "java",
        "dockerfile"    : "/data1/dockerfiles/company-news-java/Dockerfile"
    },
}
