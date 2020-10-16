const express = require('express');
const router = express.Router();
const redis = require('redis');
const redisPassword = process.env.REDIS_DB_PASSWORD;

// Create Redis Client
let redisClient = redis.createClient();
redisClient.auth(redisPassword);

redisClient.on('connect', () => {
  console.log('Connected to Redis...');
})

// Fetch home page
router.get('/', (req, res) => {
  res.render('index', { title: 'Agile Records MIS' });
});

// Add transaction
router.post('/add', (req, res) => {
  let pltNum = req.body.p_num;
  let transaction = [
    req.body.size, req.body.county, req.body.location, req.body.b_name, req.body.b_id, req.body.b_tel, req.body.s_name, req.body.s_id, req.body.s_tel, req.body.sale_val, req.body.trans_cost]

  redisClient.rpush(pltNum, transaction, (err, result) => {
      err ? console.log(err) : console.log(result)  //Change to user input
    });

  redisClient.persist(pltNum);
  res.redirect('/');
});

// Find a record
router.post('/find', (req, res) => {
  let pltSearch = req.body.query;

  redisClient.hget('trans-cache', pltSearch, (err, r) => {

    if(!r){
      res.render('index', {
        error: 'Record does not exist'
      });
    } else {

      result = JSON.parse(r);
      result.plot_no = pltSearch;

      res.render('index', {
        records: result
      });
    }
  });
  // res.redirect('/');
});

module.exports = router;
