import Header from '../components/Header/Header';
import Footer from '../components/Footer/Footer';


const NotFound = () => {
    return(
        <>
        <Header />
            <div className='centred-container'>
                <div className='centred-container__align-centred'>
                    Not found
                </div>
            </div>
        <Footer />
        </>
    );
}

export default NotFound;
