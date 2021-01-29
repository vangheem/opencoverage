export default function Footer () {
  return (
    <footer className='footer'>
      <div className='content has-text-centered'>
        <nav className='level'>
          <div className='level-item has-text-centered'>
            <div>
              <p className='heading'>
                <span className='icon'>
                  <i className='fas fa-home'></i>
                </span>
                <a href='/'>Home</a>
              </p>
            </div>
          </div>
          <div className='level-item has-text-centered'>
            <div>
              <p className='heading'>
                <span className='icon'>
                  <i className='fas fa-angle-double-down'></i>
                </span>
                <a href='/docs'>Getting started</a>
                {/* <p className='title'>789</p> */}
              </p>
            </div>
          </div>
          <div className='level-item has-text-centered'>
            <div>
              <p className='heading'>
                <span className='icon'>
                  <i className='fab fa-github'></i>
                </span>
                <a href='https://github.com/vangheem/opencoverage'>
                  Contribute
                </a>
              </p>
            </div>
          </div>
          <div className='level-item has-text-centered'>
            <div>
              <p className='heading'>
                <span className='icon'>
                  <i className='fab fa-docker'></i>
                </span>
                <a href='/docs'>Install</a>
              </p>
            </div>
          </div>
        </nav>
      </div>
    </footer>
  )
}
