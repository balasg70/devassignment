# Clone and prepare applications
git clone <spring-petclinic-repo>
git clone <python-flask-repo>

# Build and test locally
docker-compose -f container/docker-compose.local.yml up

# Run pipeline inventory
python tools/pipeline_inventory_analyzer.py legacy-ci/

# Create migration mapping
# Review mapping matrix and customize