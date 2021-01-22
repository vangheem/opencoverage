FROM node:14

WORKDIR /usr/src/app
COPY ./ ./

RUN yarn install
RUN yarn build

CMD ["yarn", "start", "--hostname", "0.0.0.0"]