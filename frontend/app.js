const createError = require('http-errors');
const express = require('express');
const https = require('https');
const path = require('path');
const cookieParser = require('cookie-parser');
const logger = require('morgan');
const expHbs = require('express-handlebars');

const indexRouter = require('./routes/index');

const app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'hbs');
app.engine( 'hbs', expHbs( {
  extname: 'hbs',
  defaultView: 'main'
}));

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

// Add routes to app
app.use('/', indexRouter);
app.use('/add', indexRouter);
app.use('/find', indexRouter);

// Initialize the backend
const req_data = {
  hostname: 'localhost',
  port: 5000,
  path: '/backend/v1',
  method: 'POST',
  headers: {'Content-Type': 'application/json'}
}

https.request(req_data, response => {
  console.log(`statusCode: ${res.statusCode}`)

  res.on('data', d => {
    process.stdout.write(d);
  })
});

// catch 404 and forward to error handler
app.use((req, res, next) => {
  next(createError(404));
});

// error handler
app.use((err, req, res, next) => {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

module.exports = app;
