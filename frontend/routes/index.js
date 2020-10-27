const express = require('express');
const redis = require('redis');

const router = express.Router();
const request = require('../app');
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

  request.get(
    `http://${backendHost}:5000/backend/v1/validate`,
    {
      json: true,
    },
    (err, response, body) => {
      console.log(`validation: ${err}, ${response.statusCode}`); // TODO:REMOVE
      if (err || response.statusCode !== 400 || response.statusCode !== 200) {
        res.render('index', {
          error: err, // TODO: Add to template
        });
      } else if (response.statusCode === 400) {
        res.render('index', {
          error: body, // TODO: Add to template
        });
      } else if (response.statusCode === 200) {
        redisClient.rpush('records_queue', JSON.stringify(transaction), (
          error,
        ) => {
          console.log(`forging: ${error}`); // TODO:REMOVE
          if (error) {
            res.render('index', {
              error: err, // TODO: Add to template
            });
          }
          redisClient.persist('records_queue');
          res.render('index', {
            success: 'Record Captured', // TODO: Add to template
          });
        });
      }
    },
  );

  // res.redirect('/');
});

// Search transaction route
router.post('/find', (req, res) => {
  const pltSearch = req.body.query;

  redisClient.hget('records_cache', pltSearch, (err, result) => {
    if (!result) {
      res.render('index', {
        error: 'Record does not exist',
      });
    } else {
      const resObj = JSON.parse(result);
      // result.plot_no = pltSearch;
      res.render('index', {
        records: resObj,
      });
    }
  });

  // res.redirect('/');
});

module.exports = router;
module.exports = backendHost;
