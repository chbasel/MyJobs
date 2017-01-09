import React from 'react';

class HelpAndTutorials extends React.Component {
  render() {
    return (
      <div className="row">
        <div className="col-xs-12 ">
          <div className="wrapper-header">
            <h2>Help & Tutorials</h2>
          </div>
          <div className="product-card-full no-highlight">
            <h3>PDF Tutorials</h3>

            <p><i className="fa fa-file-pdf-o fa-2x pull-left"></i> <a href="https://d2e48ltfsb5exy.cloudfront.net/content_mj/files/PRM+Admin+-+Quickly+add+a+User.pdf">Quickly Add a User</a><br/>
            This single page document covers the basics of adding a user to your company.</p>

            <p><i className="fa fa-file-pdf-o fa-2x pull-left"></i> <a href="https://d2e48ltfsb5exy.cloudfront.net/content_mj/files/My.jobsUserGuide-UserManagement.pdf">General Overview</a><br/>
            This comprehensive document will guide you through all the features of user management.</p>

            <h3>Video Overview</h3>

            <p>This guided overview will walk you through all the features of user management.</p>

            <div className="video-embed-container">
              <iframe src="https://player.vimeo.com/video/155433118" frameBorder="0" webkitAllowFullScreen mozallowfullscreen allowFullScreen></iframe>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default HelpAndTutorials;
