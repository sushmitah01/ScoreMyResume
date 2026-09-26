
SKILL_TAXONOMY = {
    "Python": {
        "python",
        "python 3",
        "python programming",
        "python development",
    },

    "Java": {
        "java",
        "java programming",
        "java development",
    },
    "JavaScript": {
        "javascript",
        "javascript programming",
        "js",
        "ecmascript",
    },

    "TypeScript": {
        "typescript",
        "ts",
        "typescript programming",
    },

    "C++": {
        "c++",
        "cpp",
    },

    "C#": {
        "c#",
        "c sharp",
    },

    "Go": {
        "go",
        "golang",
    },

    "Rust": {
        "rust",
        "rust programming",
    },

    "PHP": {
        "php",
        "php programming",
    },

    "Ruby": {
        "ruby",
        "ruby programming",
    },

    "SQL": {
        "sql",
        "structured query language",
    },

    "PostgreSQL": {
        "postgresql",
        "postgres",
        "postgre",
    },

    "MySQL": {
        "mysql",
    },

    "MongoDB": {
        "mongodb",
        "mongo",
    },

    "Redis": {
        "redis",
    },

    "Docker": {
        "docker",
        "docker container",
        "docker containers",
    },

    "Docker Compose": {
        "docker compose",
        "docker-compose",
    },

    "Kubernetes": {
        "kubernetes",
        "k8s",
        "kube",
    },

    "AWS": {
        "aws",
        "amazon web services",
    },

    "Azure": {
        "azure",
        "microsoft azure",
    },

    "Google Cloud": {
        "google cloud",
        "google cloud platform",
        "gcp",
    },

    "REST API": {
        "rest api",
        "rest apis",
        "restful api",
        "restful apis",
        "rest",
    },

    "GraphQL": {
        "graphql",
        "graph ql",
    },

    "FastAPI": {
        "fastapi",
        "fast api",
    },

    "Flask": {
        "flask",
    },

    "Django": {
        "django",
    },

    "Spring Boot": {
        "spring boot",
        "springboot",
    },

    "React": {
        "react",
        "react.js",
        "reactjs",
    },

    "React Native": {
        "react native",
        "react-native",
    },

    "Angular": {
        "angular",
        "angular.js",
        "angularjs",
    },

    "Vue.js": {
        "vue",
        "vue.js",
        "vuejs",
    },

    "Node.js": {
        "node",
        "node.js",
        "nodejs",
    },

    "Git": {
        "git",
        "git version control",
    },

    "GitHub": {
        "github",
    },

    "Linux": {
        "linux",
        "linux operating system",
    },

    "Machine Learning": {
        "machine learning",
        "ml",
        "machine-learning",
    },

    "Deep Learning": {
        "deep learning",
        "dl",
        "deep-learning",
    },

    "Natural Language Processing": {
        "natural language processing",
        "nlp",
        "natural-language processing",
    },

    "Computer Vision": {
        "computer vision",
        "cv",
        "computer-vision",
    },

    "PyTorch": {
        "pytorch",
        "torch",
    },

    "TensorFlow": {
        "tensorflow",
        "tf",
    },

    "Scikit-learn": {
        "scikit-learn",
        "scikit learn",
        "sklearn",
    },

    "Pandas": {
        "pandas",
    },

    "NumPy": {
        "numpy",
        "numpy python",
    },

    "Apache Spark": {
        "apache spark",
        "spark",
        "pyspark",
    },

    "Apache Kafka": {
        "apache kafka",
        "kafka",
    },

    "CI/CD": {
        "ci/cd",
        "ci cd",
        "continuous integration",
        "continuous delivery",
        "continuous deployment",
    },
    "Agile": {
        "agile",
        "agile methodology",
        "agile development",
    },

    "Scrum": {
        "scrum",
    },

    "Object-Oriented Programming": {
        "object oriented programming",
        "object-oriented programming",
        "oop",
    },
}

def build_skill_alias_map(): #resverse look up by matching alias to canonical skills 
    alias_map = {}
    for canonical_skill, aliases in SKILL_TAXONOMY.items():
        for alias in aliases:
            alias_map[alias.lower()] = canonical_skill

    return alias_map
SKILL_ALIAS_MAP = build_skill_alias_map()

#SKILL_ALIAS_MAP["postgres"] to PostgreSQL 