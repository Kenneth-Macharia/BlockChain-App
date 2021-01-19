const { Agent } = require('http');
const express = require('express');
const redis = require('redis');
const request = require('request');
const fs = require('fs');
const dateTime = require('node-datetime');

const router = express.Router();
const backendHost = process.env.BACKEND_HOST;
const redisHost = process.env.REDIS_DB_HOST;
const redisUser = process.env.REDIS_DB_USER;
const redisPassword = process.env.REDIS_DB_PASSWORD;
const cwd = process.cwd();
const currTime = dateTime.create().format('d-m-Y H:M:S');
const writer = fs.createWriteStream(`${cwd}/frontend_logs`, {
  flags: 'a',
});

// Create redis client
const redisClient = redis.createClient({
  host: redisHost,
  user: redisUser,
  password: redisPassword,
});

// Connect to redis client
redisClient.on('connect', () => {
  writer.write(`[${currTime}] Connected to the Redis database\n`);
});

// Homepage route
router.get('/', (req, res) => {
  res.render('index', {
    title: 'Agile Records MIS',
  });
});

// Search transaction route
router.post('/find', (req, res) => {
  const pltSearch = req.body.query;

  redisClient.hget('records_cache', pltSearch, (err, result) => {
    if (!result) {
      res.render('index', {
        title: 'Agile Records MIS',
        err: true,
        msg: 'Record does not exist',
        class: 'badge-danger',
      });
    } else {
      const resObj = JSON.parse(result);
      resObj.PlotNumber = pltSearch;
      res.render('index', {
        title: 'Agile Records MIS',
        data: true,
        searchRes: resObj,
      });
    }
  });
});

// Add transaction route
router.post('/add', (req, res) => {
  const transaction = {
    plot_num: req.body.p_num,
    size: req.body.size,
    county: req.body.county,
    location: req.body.location,
    buyer_name: req.body.b_name,
    buyer_id: req.body.b_id,
    buyer_tel: req.body.b_tel,
    seller_name: req.body.s_name,
    seller_id: req.body.s_id,
    seller_tel: req.body.s_tel,
    transaction_value: req.body.sale_val,
    transaction_cost: req.body.trans_cost,
  };

  // valid transaction verification
  request.post(
    `http://${backendHost}:5000/backend/v1/block`,
    {
      json: { buyer_id: transaction.buyer_id },
    },
    (err, response) => {
      if (response.statusCode === 200) {
        redisClient.rpush('records_queue', JSON.stringify(transaction), (
          error,
        ) => {
          if (!error) {
            redisClient.persist('records_queue');
            res.render('index', {
              title: 'Agile Records MIS',
              info: true,
              msg: 'Transaction queued. Check logs for save status',
              class: 'badge-info',
            });
          } else {
            res.render('index', {
              title: 'Agile Records MIS',
              err: true,
              msg: error,
              class: 'badge-danger',
            });
          }
        });
      } else {
        res.render('index', {
          title: 'Agile Records MIS',
          err: true,
          msg: response.body,
          class: 'badge-danger',
        });
      }
    },
  );
});

// Block creation logging
router.post('/alerts', (req) => {
  const resMsg = req.body;

  if ('success' in resMsg) {
    writer.write(`[${currTime}] Successfully added transaction for ${resMsg.success} to the blockchain.\n`);
  } else {
    writer.write(`[${currTime}] Adding ${resMsg.failure} to blockchain failed, contact IT for assistance.\n`);
  }
});

// Logs page route
router.get('/logs', (req, res) => {
  fs.readFile(`${cwd}/frontend_logs`, 'utf8', (err, data) => {
    const fileArray = data.split('\n');

    if (!err) {
      res.render('logs', {
        title: 'Agile Records MIS | Logs',
        contents: fileArray,
      });
    } else {
      res.render('logs', {
        title: 'Agile Records MIS | Logs',
        contents: err,
      });
    }
  });
});

exports.routing = router;
exports.fsWriter = writer;
exports.time = currTime;
