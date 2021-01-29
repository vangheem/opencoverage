export default function Menu () {
  return (
    <nav
      className='navbar is-light'
      role='navigation'
      aria-label='main navigation'
    >
      <div className='navbar-brand'>
        <a className='navbar-item' href='/'>
          <img src='/logo/logo2-trns.png' width='112' />
        </a>

        <a
          role='button'
          className='navbar-burger'
          aria-label='menu'
          aria-expanded='false'
          data-target='navbarBasicExample'
        >
          <span aria-hidden='true'></span>
          <span aria-hidden='true'></span>
          <span aria-hidden='true'></span>
        </a>
      </div>

      <div id='navbarBasicExample' className='navbar-menu'>
        <div className='navbar-start'>
          <a className='navbar-item' href='/'>
            Home
          </a>

          <a className='navbar-item' href='/docs'>
            Documentation
          </a>
        </div>
      </div>
    </nav>
  )
}
