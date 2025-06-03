WORK_DIR=`pwd`
echo $WORK_DIR
#docker-compose --env-file $WORK_DIR/.env up --build --force-recreate
#docker-compose --env-file $WORK_DIR/.env build && docker-compose --env-file $WORK_DIR/.env up
docker-compose --env-file $WORK_DIR/.env pull && docker-compose --env-file $WORK_DIR/.env build && docker-compose --env-file $WORK_DIR/.env up 



