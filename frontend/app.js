const createError = require('http-errors');
const express = require('express');
const request = require('request');
const path = require('path');
const cookieParser = require('cookie-parser');
const logger = require('morgan');
const expHbs = require('express-handlebars');
const indexRouter = require('./routes/index');

const app = express();
const backendHost = process.env.BACKEND_HOST;

// Sets our app to use the handlebars engine with .hbs file extensions
app.set('view engine', 'hbs');

// Sets handlebars configurations
app.engine('hbs', expHbs({
  layoutsDir: path.join(__dirname, '/views/layouts'),
  viewsDir: path.join(__dirname, 'views'),
  extname: 'hbs',
  defaultView: 'main',
  helpers: {},
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
app.use((err, req, res) => {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

// Initialize the backend
request.post(
  `http://${backendHost}:5000/backend/v1/init`,
  {
    json: true,
  },
  (err, res, body) => {
    if (err) {
      console.log(err.message);
    } else {
      console.log(`${res.statusCode} | ${body.message}`);
    }
  },
);

module.exports = app;
