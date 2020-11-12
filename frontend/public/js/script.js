// Functions
function btnHelper() {
  $('#addRecordForm').css('display', 'block');
  $('.badge').css('display', 'none');
  $('#addRecBtn').css('display', 'none');
  $('.search-bar').css('display', 'none');
}

(function displayAddBtn() {
  if ($('#err-badge').length !== 0) {
    $('#addRecBtn').css('display', 'block');
  } else {
    $('#addRecBtn').css('display', 'none');
  }
}());

(function displayAddTransBtn() {
  if ($('#findRecords table').html() !== undefined) {
    $('#addTransBtn').css('display', 'block');
  } else {
    $('#addTransBtn').css('display', 'none');
  }
}());

(function displayVideoDemo() {
  // eslint-disable-next-line no-restricted-globals
  const urlPath = location.pathname;

  if (urlPath === '/') {
    $('.jumbotron').css('display', 'block');
    $('.body').css('background-color', '#FFFFFF');
  } else {
    $('.jumbotron').css('display', 'none');
    $('.body').css('background-color', '#EAECEF');
  }
}());

// Events
$('#addRecBtn').click((e) => {
  e.preventDefault();
  btnHelper();
});

$('#addTransBtn').click((e) => {
  e.preventDefault();
  btnHelper();
});

$('#county').change(function selectCall() {
  // eslint-disable-next-line default-case
  switch (this.value) {
    case 'Nairobi':
      $('#location').find('option').remove().end();
      $('#location').append(new Option('Choose...', ''));
      $('#location').append(new Option('Dagoretti', 'Dagoretti'));
      $('#location').append(new Option('Kangemi', 'Kangemi'));
      $('#location').append(new Option('Langata', 'Langata'));
      break;

    case 'Kiambu':
      $('#location').find('option').remove().end();
      $('#location').append(new Option('Choose...', ''));
      $('#location').append(new Option('Kikuyu', 'Kikuyu'));
      $('#location').append(new Option('Thika', 'Thika'));
      $('#location').append(new Option('Limuru', 'Limuru'));
      break;

    case 'Nyeri':
      $('#location').find('option').remove().end();
      $('#location').append(new Option('Choose...', ''));
      $('#location').append(new Option('Othaya', 'Othaya'));
      $('#location').append(new Option('Karatina', 'Karatina'));
      $('#location').append(new Option('Mwiga', 'Mwiga'));
      break;

    default:
      $('#location').find('option').remove().end();
      $('#location').append(new Option('Choose...', ''));
  }
});
