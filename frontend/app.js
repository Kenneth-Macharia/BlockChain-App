const createError = require('http-errors');
const express = require('express');
const request = require('request');
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

// Initialize the backend
// const req_data = {
//   hostname: 'backend_1',
//   port: 5000,
//   path: '/backend/v1/init',
//   method: 'POST'
// }
// http.request(req_data, response => {
//   console.log(`statusCode: ${res.statusCode}`)

//   res.on('data', d => {
//     process.stdout.write(d);
//   })
// });

request.post(
  'http://backend_1:5000/backend/v1/init',
  {
    json: true
  },
  (err, res, body) => {
    if (err) {
      return console.log(err);
    }

    console.log(`statusCode: ${res.statusCode}`)
    console.log(res, body);
});

module.exports = app;
