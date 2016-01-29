var Submission = React.createClass({
  getInitialState: function() {
    return {
      submission: null,
    };
  },

  checkForUpdates: function() {
    $.get('/submission/' + this.props.id + '.json', function(data) {
      this.setState({ submission: data });
    }.bind(this));
  },

  componentDidMount: function() {
    this.checkForUpdates();
    setInterval(this.checkForUpdates, 5000);
  },

  render: function() {
    var submission = this.state.submission;

    var status = "";
    var extra;
    if (!submission) {
      status = <span className="label label-info">Loading...</span>;
    } else if (submission.status === 'waiting') {
      status = <span className="label label-info">Waiting for judge</span>;
    } else if (submission.status === 'running') {
      status = <span className="label label-info">Currently Running</span>;
    } else if (submission.status == 'passed') {
      status = <span className="label label-success">All tests passed</span>;
    } else if (submission.status == 'failed') {
      status = <span className="label label-danger">Tests failed. Check output</span>;
      extra = <a href={'/submission/' + this.props.id + '/out'}>View Output</a>;
    } else {
      status = <span className="label label-danger">Tests timed out</span>;
    }

    return (
      <div>
        <h3>Status: {status}</h3>
        <br />
        {extra}
      </div>
    );
  },
});

ReactDOM.render(<Submission id={$('#id').val()} />, $('#mount').get(0));
