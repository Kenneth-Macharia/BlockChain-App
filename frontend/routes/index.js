const express = require('express');
const redis = require('redis');
const request = require('request');

const router = express.Router();
const backendHost = process.env.BACKEND_HOST;
const redisHost = process.env.REDIS_DB_HOST;
const redisUser = process.env.REDIS_DB_USER;
const redisPassword = process.env.REDIS_DB_PASSWORD;

// Create redis client
const redisClient = redis.createClient({
  host: redisHost,
  user: redisUser,
  password: redisPassword,
});

// Connect to redis client
redisClient.on('connect', () => {
  console.log('Connected to Redis...');
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
    value: req.body.sale_val,
    transaction_cost: req.body.trans_cost,
  };

  let cacheErr = '';

  // unique transaction verification
  request.post(
    `http://${backendHost}:5000/backend/v1/block`,
    {
      json: {
        plot_number: transaction.plot_num,
        buyer_id: transaction.buyer_id,
        seller_id: transaction.seller_id,
      },
    },
    (err, response, body) => {
      if (response.statusCode === 200) {
        redisClient.rpush('records_queue', JSON.stringify(transaction), (
          error,
        ) => {
          if (!error) {
            redisClient.persist('records_queue');
          } else {
            cacheErr = error;
          }
        });
      } else if (response.statusCode === 400) {
        cacheErr = body;
      } else {
        cacheErr = err;
      }
    },
  );

  if (!cacheErr) {
    res.render('index', {
      title: 'Agile Records MIS',
      info: true,
      msg: 'Transaction captured',
      class: 'badge-info',
    });
  } else {
    res.render('index', {
      title: 'Agile Records MIS',
      err: true,
      msg: cacheErr,
      class: 'badge-danger',
    });
  }
});

// Backend notifications
router.post('/alerts', (req, res) => {
  const resMsg = req.body;

  if ('success' in resMsg) {
    res.render('index', {
      title: 'Agile Records MIS',
      info: true,
      msg: `Transaction for ${resMsg.success} added to blockchain`,
      class: 'badge-info',
    });
  } else {
    console.log(resMsg.failure);
    res.render('index', {
      title: 'Agile Records MIS',
      err: true,
      msg: `Adding ${resMsg.failure} to blockchain failed, contact IT`,
      class: 'badge-danger',
    });
  }
  // res.redirect('/');
});

module.exports = router;
