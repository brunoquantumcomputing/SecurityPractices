use argon2::{
    password_hash::{rand_core::OsRng, PasswordHash, PasswordHasher, PasswordVerifier},
    Argon2,
};
use secrecy::{Secret, ExposeSecret};
use serde::{Deserialize, Serialize};
use std::error::Error;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PasswordHash {
    hash: String,
}

impl PasswordHash {
    pub fn new(password: Secret<String>) -> Result<Self, Box<dyn Error>> {
        let salt = rand::thread_rng().gen::<[u8; 32]>();
        let argon2 = Argon2::default();
        
        let hash = argon2.hash_password(
            password.expose_secret().as_bytes(),
            &salt,
        )?;
        
        Ok(Self {
            hash: hash.to_string(),
        })
    }
    
    pub fn verify(&self, password: Secret<String>) -> Result<(), Box<dyn Error>> {
        let parsed_hash = PasswordHash::new(&self.hash)?;
        parsed_hash.verify_password(password.expose_secret().as_bytes())?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use secrecy::Secret;
    
    #[test]
    fn test_password_hash() {
        let password = Secret::new("correct-horse-battery-staple".to_string());
        let hash = PasswordHash::new(password.clone()).unwrap();
        
        assert!(hash.verify(password.clone()).is_ok());
        assert!(hash.verify(Secret::new("wrong-password".to_string())).is_err());
    }
}