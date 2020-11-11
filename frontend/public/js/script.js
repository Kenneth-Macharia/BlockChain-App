// Events
$('#addRecBtn').click((e) => {
  e.preventDefault();
  $('#addRecordForm').css('display', 'block');
  $('#info-badge').css('display', 'none');
  $('#addRecBtn').css('display', 'none');
  $('.search-bar').css('display', 'none');
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
  }
});

// Functions
(function displayAddBtn() {
  if ($('#err-badge').length !== 0) {
    $('#addRecBtn').css('display', 'block');
  } else {
    $('#addRecBtn').css('display', 'none');
  }
}());
