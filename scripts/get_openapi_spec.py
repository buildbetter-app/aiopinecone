import requests
import yaml

URLS_AND_PATHS = [
    (
        "https://docs.pinecone.io/reference/list_collections?json=on",
        "../public/openapi.yml",
    ),
]


def download_openapi_spec(url: str):
    sess = requests.Session()
    response = sess.get(url)
    if response.status_code == 200:
        data = response.json()
    else:
        raise Exception(f"Failed to download OpenAPI specs from {url}")
    return data["oasDefinition"]


def _fix_array_lengths(doc):
    if isinstance(doc, dict):
        if "type" in doc and doc["type"] == "array":
            if "minLength" in doc:
                del doc["minLength"]
            if "maxLength" in doc:
                del doc["maxLength"]
        for key, value in list(doc.items()):
            doc[key] = _fix_array_lengths(value)
    elif isinstance(doc, list):
        for i, value in enumerate(doc):
            doc[i] = _fix_array_lengths(value)
    return doc


def process_openapi_spec(spec: dict):
    spec = _fix_array_lengths(spec)
    return spec


def write_openapi_spec(spec: dict, path: str):
    with open(path, "w") as f:
        f.write(yaml.dump(spec))


if __name__ == "__main__":
    for url, path in URLS_AND_PATHS:
        spec = download_openapi_spec(url)
        spec = process_openapi_spec(spec)
        write_openapi_spec(spec, path)
