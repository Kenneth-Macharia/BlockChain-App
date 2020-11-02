// functions
function sectionDisplay(param) {
  const sections = $('.container-fluid');

  // eslint-disable-next-line no-restricted-syntax
  for (const section of sections) {
    if (section.getAttribute('id') === param) {
      // $('#section-heading').html(titleMap[param]);
      section.style.display = 'block';
    } else {
      section.style.display = 'none';
    }
  }
}

// Section selection on app routing
const sectionParam = window.location.pathname.replace('/', '');
// eslint-disable-next-line default-case
switch (sectionParam) {
  case '':
    sectionDisplay('find');
    break;

  case 'add':
    sectionDisplay('add');
    break;
}

// Add section county & location drop-down options
$('#county').change(() => {
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
