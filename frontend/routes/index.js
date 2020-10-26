const express = require('express');
const redis = require('redis');

const router = express.Router();
const redisHost = process.env.REDIS_DB_HOST;
const redisUser = process.env.REDIS_DB_USER;
const redisPassword = process.env.REDIS_DB_PASSWORD;

// Redis Client
const redisClient = redis.createClient({
  host: redisHost,
  user: redisUser,
  password: redisPassword,
});

redisClient.on('connect', () => {
  console.log('Connected to Redis...');
});

// Routes
router.get('/', (req, res) => {
  res.render('index', { title: 'Agile Records MIS' });
});

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

  redisClient.rpush('records_queue', JSON.stringify(transaction), (
    err,
  ) => {
    if (err) {
      console.error(err);
    } else {
      redisClient.persist('records_queue');
      // res.redirect('/');
      res.render('index', {
        success: 'Record Captured', // TODO: Add to template
      });
    }
  });
});

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
