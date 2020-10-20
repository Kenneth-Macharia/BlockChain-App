const { response } = require('express');
const express = require('express');
const router = express.Router();
const redis = require('redis');
const redisHost = process.env.REDIS_DB_HOST;
const redisUser = process.env.REDIS_DB_USER;
const redisPassword = process.env.REDIS_DB_PASSWORD;

// Create Redis Client
let redisClient = redis.createClient({
  host: redisHost,
  user: redisUser,
  password: redisPassword
});

redisClient.on('connect', () => {
  console.log('Connected to Redis...');
})

// Fetch home page
router.get('/', (req, res) => {
  res.render('index', { title: 'Agile Records MIS' });
});

// Add transaction
router.post('/add', (req, res) => {

  let transaction = {
    'plot_num': req.body.p_num,
    'size': req.body.size,
    'county': req.body.county,
    'location': req.body.location,
    'buyer_name': req.body.b_name,
    'buyer_id': req.body.b_id,
    'buyer_tel': req.body.b_tel,
    'seller_name': req.body.s_name,
    'seller_id': req.body.s_id,
    'seller_tel': req.body.s_tel,
    'value': req.body.sale_val,
    'transaction_cost': req.body.trans_cost
  }

  redisClient.rpush('records_queue', JSON.stringify(transaction), (
    err, result) => {
      err ? console.log(err) : console.log(result)  //Change to user input
    });

  redisClient.persist('records_queue');
  res.redirect('/');
});

// Find a record
router.post('/find', (req, res) => {
  let pltSearch = req.body.query;

  redisClient.hget('records_cache', pltSearch, (err, result) => {

    if(!result){
      console.log(err);
      res.render('index', {
        error: 'Record does not exist'
      });
    } else {
      res_obj = JSON.parse(result);
      result.plot_no = pltSearch;

      res.render('index', {
        records: res_obj
      });
    }
  });
  // res.redirect('/');
});

module.exports = router;
