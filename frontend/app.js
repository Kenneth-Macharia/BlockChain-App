const createError = require('http-errors');
const express = require('express');
const request = require('request');
const path = require('path');
const cookieParser = require('cookie-parser');
const logger = require('morgan');
const expHbs = require('express-handlebars');
const indexRouter = require('./routes/index');

const backendHost = process.env.BACKEND_HOST;

// create express app
const app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'hbs');
app.engine('hbs', expHbs({
  extname: 'hbs',
  defaultView: 'main',
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

// catch 404 and forward to error handler
app.use((next) => {
  next(createError(404));
});

// error handler
app.use((err, req, res) => {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

// Initialize the backend
// request.post(
//   `http://${backendHost}:5000/backend/v1/init`,
//   {
//     json: true,
//   },
//   (err, res, body) => {
//     if (err) {
//       return console.log(err);
//     }
//     return console.log(res.statusCode, body);
//   },
// );

module.exports = app;
