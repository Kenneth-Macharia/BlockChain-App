// Functions
function btnHelper() {
  $('.badge').css('display', 'none');
  $('#addRecBtn').css('display', 'none');
  $('.search-bar').css('display', 'none');
  $('#findRecords').css('display', 'none');
  $('#addRecordForm').css('display', 'block');
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
    sessionStorage.setItem('pltNum', $('#findRecords table').find('tr:eq(1)').find('td:eq(0)').html());
    sessionStorage.setItem('sellerName', $('#findRecords table').find('tr:eq(1)').find('td:eq(1)').html());
    sessionStorage.setItem('sellerId', $('#findRecords table').find('tr:eq(1)').find('td:eq(2)').html());
    sessionStorage.setItem('sellerTel', $('#findRecords table').find('tr:eq(1)').find('td:eq(3)').html());
    sessionStorage.setItem('county', $('#findRecords table').find('tr:eq(1)').find('td:eq(4)').html());
    sessionStorage.setItem('location', $('#findRecords table').find('tr:eq(1)').find('td:eq(5)').html());
    sessionStorage.setItem('size', $('#findRecords table').find('tr:eq(1)').find('td:eq(6)').html());
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
  $('#plot_num').val(sessionStorage.getItem('searchPltNum'));
  $('#plot_num').focus();
});

$('#addTransBtn').click((e) => {
  e.preventDefault();
  btnHelper();
  $('#county').val(sessionStorage.getItem('county'));
  $('#county').trigger('change');
  $('#plot_num').val(sessionStorage.getItem('pltNum'));
  $('#size').val(sessionStorage.getItem('size'));
  $('#seller-name').val(sessionStorage.getItem('sellerName'));
  $('#seller-id').val(sessionStorage.getItem('sellerId'));
  $('#seller-tel').val(sessionStorage.getItem('sellerTel'));
  $('#location').val(sessionStorage.getItem('location'));
  $('.protect').prop('disabled', true);
  $('#buyer-name').focus();
});

$('#searchBtn').click(() => {
  sessionStorage.setItem('searchPltNum', $('#searchInput').val());
});

$('#addRecordForm form').submit(() => {
  $('.protect').prop('disabled', false);
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
