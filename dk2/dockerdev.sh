set -e
# set -x

cd "$(dirname $0)"

while getopts "p:P:e:" opt; do
    case $opt in
    p)
        port="$OPTARG"
        ;;
    P)
        pythonpath="$OPTARG"
        ;;
    e)
        dockerenvarg="-e $OPTARG $dockerenvarg"
        ;;
    esac
done
shift $(($OPTIND - 1))

if [ -n "$port" ]; then
    portarg="-p $port:$port"
fi

if [ -n "$pythonpath" ]; then
    pythonpatharg="-e PYTHONPATH=$pythonpath"
fi

dev_path=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
dev_path=/MyJobs/gulp/node_modules/.bin:$dev_path

init() {
    initsolrdata
    initmysqldata
    initrevproxycerts
    initmongodata
    initnet
}

initsolrdata() {
    docker build -t darrint/solrdata solrdata
    docker create --name solrdata darrint/solrdata true
}

initmysqldata() {
    docker build -t darrint/mysqldata mysqldata
    docker create --name mysqldata darrint/mysqldata true
}

initmongodata() {
    docker build -t darrint/mongodata mongodata
    docker create --name mongodata darrint/mongodata true
}

initrevproxycerts() {
    keydir=revproxy/certs
    mkdir -p $keydir
    for vhost in "jobs" secure.my.jobs; do
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -subj "/C=us/CN=$vhost" \
            -keyout $keydir/$vhost.key -out $keydir/$vhost.crt
    done
}

initnet() {
  docker network create myjobs
}

debugargs() {
    echo "$port $portarg $pythonpath $pythonpatharg ||| $@"
}

pull() {
    docker pull mysql:5.5
    docker pull ubuntu:14.04
    docker pull ubuntu:15.10
    docker pull nginx:stable
}

background() {
    docker build \
        -t darrint/solr \
        solr
    docker build \
         -t myjobsdev/revproxy \
         nginx-proxy
    docker run \
        --name solr \
        --net=myjobs \
        -d \
        --volumes-from solrdata \
        -p 8983:8983 \
        darrint/solr
    docker run \
        --name mysql \
        --net=myjobs \
        -d \
        -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD \
        --volumes-from mysqldata \
        --expose=3306 \
        -p 3306:3306 \
        mysql:5.5
    docker run \
        --name revproxy \
        --net=myjobs \
        -d \
        -p 80:80 -p 443:443 \
        -v $(pwd)/revproxy/certs:/etc/nginx/certs \
        -v /var/run/docker.sock:/tmp/docker.sock:ro \
        myjobsdev/revproxy
    docker run \
        --name mongo \
        --net=myjobs \
        -d \
        --volumes-from mongodata \
        -p 27017:27017 \
        mongo:3.2
}

backgroundstop() {
    docker stop mysql || true
    # Avoid timeout on our hacky solr container.
    docker kill solr || true
    docker stop revproxy || true
    docker stop mongo || true
    docker rm mysql || true
    docker rm solr || true
    docker rm revproxy || true
    docker rm mongo || true
}

bgrst() {
    backgroundstop || true
    background || true
}

restartsecure() {
    docker stop django-secure || true
    docker rm django-secure || true
    runsecure || true
}

restartmicrosites() {
    docker stop django-microsites || true
    docker rm django-microsites || true
    runmicrosites || true
}

restartredirect() {
    docker stop django-redirect || true
    docker rm django-redirect || true
    runredirect || true
}

maint() {
    docker run \
        --rm \
        --net=myjobs \
        --volumes-from solrdata \
        --volumes-from mysqldata \
        -v $(pwd)/..:/MyJobs \
        -v $(pwd)/../../deployment:/deployment \
        -w=/MyJobs \
        -it \
        "$1" \
        /bin/bash
}

rebuilddev() {
    cp -p ../requirements.txt dev
    time docker build -t darrint/dev dev
}

doruncd() {
    dir="$1"
    shift
    docker run \
        --rm \
        --net=myjobs \
        -v $(pwd)/..:/MyJobs \
        -v $(pwd)/../../deployment:/deployment \
        $portarg \
        $pythonpatharg \
        $dockerenvarg \
        -w /MyJobs/"$dir" \
        -e PATH="$dev_path" \
        -e npm_config_unsafe_perm=1 \
        -i -t \
        darrint/dev "$@"
}

dorun() {
    doruncd . "$@"
}

manage() {
    dorun python manage.py "$@"
}

runserver() {
    virthost="$1"
    docker run \
        --name $virthost \
        --net=myjobs \
        --expose=8000 \
        --rm \
        -v $(pwd)/..:/MyJobs \
        -v $(pwd)/../../deployment:/deployment \
        $pythonpatharg \
        $dockerenvarg \
        -w /MyJobs \
        -i -t \
        darrint/dev \
        python manage.py runserver 0.0.0.0:8000
}

runmicrosites() {
    pythonpatharg="-e PYTHONPATH=settings_dseo" \
        runserver "django-microsites"
}

runsecure() {
    pythonpatharg="-e PYTHONPATH=settings_myjobs" \
        runserver "django-secure"
}

runredirect() {
    pythonpatharg="-e PYTHONPATH=settings_redirect" \
        runserver "django-redirect"
}

rundevserver() {
    docker run \
        --net=myjobs \
        --name webpack-devserver \
        --rm \
        -v $(pwd)/..:/MyJobs \
        -v $(pwd)/../../deployment:/deployment \
        $pythonpatharg \
        $dockerenvarg \
        --user $(id -u):$(id -g) \
        -p 8080:8080 \
        -w /MyJobs/gulp \
        -i -t \
        darrint/dev \
        npm run devserver
}

"$@"
