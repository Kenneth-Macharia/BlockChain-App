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
  res.render('index', { title: 'Agile Records MIS' });
});

// Search transaction route
router.post('/find', (req, res) => {
  const pltSearch = req.body.query;

  redisClient.hget('records_cache', pltSearch, (err, result) => {
    if (!result) {
      res.render('index', {
        info: true,
        message: 'Record does not exist',
        class: 'badge-danger',
      });
    } else {
      const resObj = JSON.parse(result);
      res.render('index', {
        records: resObj,
      });
    }
  });

  // res.redirect('/');
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

  // unique transaction validation
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
          if (error) {
            response.render('index', {
              error: err,
            });
          } else {
            redisClient.persist('records_queue');
            response.render('index', {
              info: 'Record Captured',
            });
          }
        });
      } else if (response.statusCode === 400) {
        response.render('index', {
          error: body,
        });
      } else {
        response.render('index', {
          error: err,
        });
      }
    },
  );

  // res.redirect('/');
});

module.exports = router;
