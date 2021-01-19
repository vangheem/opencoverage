import Header from '../components/header'
import Footer from '../components/footer'
import Report from '../components/report'
import useSWR from 'swr'
import { fetcher, apiUrl } from '../utils'

export default function Home () {
  const { data, error } = useSWR(`${apiUrl}/recent-pr-reports`, fetcher)
  if (!data) {
    return <ul />
  }

  return (
    <div className='container'>
      <Header />

      {data.result.map((report, index) => {
        return <Report report={report} key={index} />
      })}

      <Footer />
    </div>
  )
}
