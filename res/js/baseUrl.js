const baseUrl = (location.host === 'localhost') ? ''
    : !!location.port ? ''
    : (location.protocol + '//' + location.host + ':8000');

window.baseUrl = baseUrl;
