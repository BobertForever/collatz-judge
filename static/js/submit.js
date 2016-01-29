var cm = CodeMirror($('#editor').get(0), {
  mode: 'python',
});

$('#submit').on('click', function() {
  alert(cm.getValue());
}.bind(cm));
