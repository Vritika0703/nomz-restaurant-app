import { useState } from 'react';
import { motion } from 'motion/react';
import { SignIn } from './components/SignIn';
import { SignUp } from './components/SignUp';
import { Home } from './components/Home';
import { UserHome } from './components/UserHome';
import { RestaurantProfile } from './components/RestaurantProfile';
import { UserProfile } from './components/UserProfile';
import { Messages } from './components/Messages';
import { Map } from './components/Map';
import { PhotoManagement } from './components/PhotoManagement';
import { AdminDashboard } from './components/AdminDashboard';
import { AdminModeration } from './components/AdminModeration';
import { AdminPendingApprovals } from './components/AdminPendingApprovals';
import { AdminManageUsers } from './components/AdminManageUsers';
import { AdminLogs } from './components/AdminLogs';
import { PasswordResetForm } from './components/PasswordResetForm';
import { PasswordResetDone } from './components/PasswordResetDone';
import { PasswordResetConfirm } from './components/PasswordResetConfirm';
import { PasswordResetComplete } from './components/PasswordResetComplete';
import { ManageActivation } from './components/ManageActivation';
import { TwoFactorAuth } from './components/TwoFactorAuth';

type View = 'opening' | 'home' | 'signin' | 'signup' | 'userhome' | 'restaurantprofile' | 'userprofile' | 'messages' | 'map' | 'restaurantmap' | 'photomanagement' | 'admin' | 'adminmoderation' | 'adminapprovals' | 'adminusers' | 'adminlogs' | 'adminmap' | 'passwordreset' | 'passwordresetdone' | 'passwordresetconfirm' | 'passwordresetcomplete' | 'manageactivation' | 'twofactorauth';

interface UserData {
  username: string;
  accountType: 'diner' | 'restaurant';
}

export default function App() {
  const [view, setView] = useState<View>('opening');
  const [showClickToStart, setShowClickToStart] = useState(false);
  const [userData, setUserData] = useState<UserData | null>(null);

  const handleAnimationEnd = () => {
    setShowClickToStart(true);
  };

  const handleClick = () => {
    if (view === 'opening' && showClickToStart) {
      setView('home');
    }
  };

  const handleSignInClick = () => {
    setView('signin');
  };

  const handleSignUpClick = () => {
    setView('signup');
  };

  const handleBackToHome = () => {
    setView('home');
  };

  const handleSignIn = (accountType: 'diner' | 'restaurant', username: string) => {
    setUserData({ username, accountType });
    if (accountType === 'diner') {
      setView('userhome');
    } else {
      setView('restaurantprofile');
    }
  };

  const handleSignUp = (accountType: 'diner' | 'restaurant', username: string) => {
    setUserData({ username, accountType });
    if (accountType === 'diner') {
      setView('userhome');
    } else {
      setView('restaurantprofile');
    }
  };

  const handleLogout = () => {
    setUserData(null);
    setView('home');
  };

  const handleViewProfile = () => {
    setView('userprofile');
  };

  const handleBackToUserHome = () => {
    setView('userhome');
  };

  const handleViewMessages = () => {
    setView('messages');
  };

  const handleNavigateMap = () => {
    setView('map');
  };

  const handlePhotoManagement = () => {
    setView('photomanagement');
  };

  const handleViewAdmin = () => {
    setView('admin');
  };

  const handleViewModeration = () => {
    setView('adminmoderation');
  };

  const handleViewPendingApprovals = () => {
    setView('adminapprovals');
  };

  const handleViewManageUsers = () => {
    setView('adminusers');
  };

  const handleViewAdminLogs = () => {
    setView('adminlogs');
  };

  const handleAdminBack = () => {
    setView('admin');
  };

  const handleAdminMapBack = () => {
    setView('admin');
  };

  const handleAdminMapAccess = () => {
    setView('adminmap');
  };

  const handleForgotPassword = () => {
    setView('passwordreset');
  };

  const handlePasswordResetSubmit = () => {
    setView('passwordresetdone');
  };

  const handlePasswordResetConfirm = () => {
    setView('passwordresetconfirm');
  };

  const handlePasswordResetComplete = () => {
    setView('passwordresetcomplete');
  };

  const handlePasswordResetToLogin = () => {
    setView('signin');
  };

  const handleManageActivation = () => {
    setView('manageactivation');
  };

  const handleActivationToggle = () => {
    setView('restaurantprofile');
  };

  const handleTwoFactorAuth = () => {
    setView('twofactorauth');
  };

  const handleTwoFactorVerify = () => {
    // After 2FA is verified, redirect to appropriate home page
    if (userData?.accountType === 'restaurant') {
      setView('restaurantprofile');
    } else {
      setView('userhome');
    }
  };

  if (view === 'adminlogs') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <AdminLogs onBack={handleAdminBack} />
      </div>
    );
  }

  if (view === 'adminusers') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <AdminManageUsers onBack={handleAdminBack} />
      </div>
    );
  }

  if (view === 'adminapprovals') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <AdminPendingApprovals onBack={handleAdminBack} />
      </div>
    );
  }

  if (view === 'adminmoderation') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <AdminModeration onBack={handleAdminBack} />
      </div>
    );
  }

  if (view === 'admin') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <AdminDashboard 
          onLogout={handleLogout}
          onNavigateMap={handleAdminMapAccess}
          onViewModeration={handleViewModeration}
          onViewPendingApprovals={handleViewPendingApprovals}
          onViewPendingUsers={handleViewManageUsers}
          onViewLogs={handleViewAdminLogs}
        />
      </div>
    );
  }

  if (view === 'adminmap') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <Map 
          onNavigateHome={handleAdminMapBack}
          onNavigateMessages={handleAdminMapBack}
          onNavigateProfile={handleAdminMapBack}
          onLogout={handleLogout}
          isAdmin={true}
        />
      </div>
    );
  }

  if (view === 'photomanagement') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <PhotoManagement onBack={() => setView('restaurantprofile')} />
      </div>
    );
  }

  if (view === 'map') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <Map 
          onNavigateHome={handleBackToUserHome}
          onNavigateMessages={handleViewMessages}
          onNavigateProfile={handleViewProfile}
          onLogout={handleLogout}
          isAdmin={false}
        />
      </div>
    );
  }

  if (view === 'messages') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <Messages 
          onNavigateMap={handleNavigateMap}
          onNavigateHome={userData?.accountType === 'restaurant' ? () => setView('restaurantprofile') : handleBackToUserHome}
          onNavigateProfile={handleViewProfile}
          onLogout={handleLogout}
          accountType={userData?.accountType === 'restaurant' ? 'Restaurant' : 'Diner'}
        />
      </div>
    );
  }

  if (view === 'userprofile') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <UserProfile 
          onBack={handleBackToUserHome} 
          onViewMessages={handleViewMessages}
          onNavigateMap={handleNavigateMap}
          onNavigateHome={() => setView('home')}
          username={userData?.username || 'Diner'} 
        />
      </div>
    );
  }

  if (view === 'userhome') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <UserHome 
          onLogout={handleLogout} 
          onViewProfile={handleViewProfile}
          onViewMessages={handleViewMessages}
          onNavigateMap={handleNavigateMap}
          username={userData?.username || 'Diner'} 
        />
      </div>
    );
  }

  if (view === 'restaurantprofile') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <RestaurantProfile 
          onLogout={handleLogout} 
          username={userData?.username || 'Restaurant'} 
          onNavigateMessages={handleViewMessages}
          onPhotoManagement={handlePhotoManagement}
          onNavigateMap={handleNavigateMap}
          onNavigateRestaurantMap={() => setView('restaurantmap')}
          onBack={() => setView('restaurantprofile')}
          onManageActivation={handleManageActivation}
        />
      </div>
    );
  }

  if (view === 'restaurantmap') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <Map 
          onNavigateHome={() => setView('restaurantprofile')}
          onNavigateMessages={handleViewMessages}
          onNavigateProfile={() => setView('restaurantprofile')}
          onLogout={handleLogout}
          isAdmin={false}
        />
      </div>
    );
  }

  if (view === 'twofactorauth') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <TwoFactorAuth 
          onBack={handleSignInClick}
          onVerify={handleTwoFactorVerify}
          onResend={() => console.log('Resending 2FA code')}
        />
      </div>
    );
  }

  if (view === 'manageactivation') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <ManageActivation 
          onBack={handleActivationToggle}
          isActive={true}
          onToggle={handleActivationToggle}
        />
      </div>
    );
  }

  if (view === 'passwordresetcomplete') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <PasswordResetComplete onLoginClick={handlePasswordResetToLogin} />
      </div>
    );
  }

  if (view === 'passwordresetconfirm') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <PasswordResetConfirm 
          onBack={handlePasswordResetToLogin} 
          onSubmit={handlePasswordResetComplete}
          isValidLink={true}
        />
      </div>
    );
  }

  if (view === 'passwordresetdone') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <PasswordResetDone onBack={handlePasswordResetToLogin} />
      </div>
    );
  }

  if (view === 'passwordreset') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <PasswordResetForm 
          onBack={handleBackToHome} 
          onSubmit={handlePasswordResetSubmit}
        />
      </div>
    );
  }

  if (view === 'signin') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <SignIn 
          onBackClick={handleBackToHome} 
          onSignIn={handleSignIn}
          onForgotPassword={handleForgotPassword}
        />
      </div>
    );
  }

  if (view === 'signup') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <SignUp onBackClick={handleBackToHome} onSignUp={handleSignUp} />
      </div>
    );
  }

  if (view === 'home') {
    return (
      <div className="h-screen w-screen overflow-hidden">
        <Home 
          onSignInClick={handleSignInClick} 
          onSignUpClick={handleSignUpClick}
          onAdminAccess={handleViewAdmin}
        />
      </div>
    );
  }

  return (
    <div 
      className="size-full flex items-center justify-center cursor-pointer" 
      style={{ backgroundImage: 'radial-gradient(circle, #E06E7F, #FFF9F5)' }}
      onClick={handleClick}
    >
      <div className="flex flex-col items-center gap-2">
        <div className="flex items-center gap-2">
          {['n', 'o', 'm', 'z'].map((letter, index) => (
            <motion.span
              key={index}
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ 
                opacity: 1, 
                scale: [0.5, 1.2, 1],
              }}
              transition={{
                duration: 0.8,
                delay: index * 0.15,
                ease: "easeOut"
              }}
              className="text-4xl text-white"
              style={{ 
                fontFamily: 'Montserrat, sans-serif',
                filter: 'drop-shadow(0 0 8px rgba(224, 110, 127, 0.6))'
              }}
            >
              {letter}
            </motion.span>
          ))}
        </div>
        
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{
            duration: 0.5,
            delay: 1.1,
            ease: "easeIn"
          }}
          onAnimationComplete={handleAnimationEnd}
          className="text-xs text-white"
          style={{ 
            fontFamily: 'Montserrat, sans-serif'
          }}
        >
          click to start
        </motion.p>
      </div>
    </div>
  );
}